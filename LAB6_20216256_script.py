import json
import yaml
import requests
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict

# Floodlight controller configuration
CONTROLLER_IP = "192.168.200.200"
CONTROLLER_PORT = 8080
CONTROLLER_URL = f"http://{CONTROLLER_IP}:{CONTROLLER_PORT}"

conexiones = []

BASE_URL = f"http://{CONTROLLER_IP}:8080"
HEADERS = {'Content-Type': 'application/json'}

@dataclass
class Alumno:
    nombre: str
    codigo: int
    mac: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Alumno':
        return Alumno(
            nombre=data['nombre'],
            codigo=int(data['codigo']),
            mac=data['mac']
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Servicio:
    nombre: str
    protocolo: str
    puerto: int

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Servicio':
        return Servicio(
            nombre=data['nombre'],
            protocolo=data['protocolo'],
            puerto=int(data['puerto'])
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Servidor:
    nombre: str
    ip: str
    servicios: List[Servicio] = field(default_factory=list)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Servidor':
        servicios = [Servicio.from_dict(s) for s in data.get('servicios', [])]
        return Servidor(
            nombre=data['nombre'],
            ip=data['ip'],
            servicios=servicios
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'nombre': self.nombre,
            'ip': self.ip,
            'servicios': [s.to_dict() for s in self.servicios]
        }


@dataclass
class Curso:
    codigo: str
    estado: str
    nombre: str
    alumnos: List[int]
    servidores: List[Dict[str, Any]]

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Curso':
        return Curso(
            codigo=data['codigo'],
            estado=data['estado'],
            nombre=data['nombre'],
            alumnos=[int(cod) for cod in data.get('alumnos', [])],
            servidores=data.get('servidores', [])
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigo': self.codigo,
            'estado': self.estado,
            'nombre': self.nombre,
            'alumnos': self.alumnos,
            'servidores': self.servidores
        }


def importar_yaml(nombre_archivo):
    global alumnos, cursos, servidores
    with open(nombre_archivo, 'r') as f:
        data = yaml.safe_load(f)

    alumnos = [Alumno.from_dict(a) for a in data.get('alumnos', [])]
    cursos = [Curso.from_dict(c) for c in data.get('cursos', [])]
    servidores = [Servidor.from_dict(s) for s in data.get('servidores', [])]


def exportar_yaml(nombre_archivo, alumnos, cursos, servidores):
    data = {
        'alumnos': [a.to_dict() for a in alumnos],
        'cursos': [c.to_dict() for c in cursos],
        'servidores': [s.to_dict() for s in servidores]
    }
    with open(nombre_archivo, 'w') as f:
        yaml.dump(data, f)

def menu_cursos():
    global cursos, alumnos

    while True:
        print("\n--- MENÚ CURSOS ---")
        print("1) Listar cursos")
        print("2) Mostrar detalle de un curso")
        print("3) Actualizar curso (agregar/eliminar alumno)")
        print("0) Volver")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Lista de cursos ---")
            for c in cursos:
                print(f"- {c.codigo}: {c.nombre} [{c.estado}]")

        elif opcion == '2':
            codigo = input("Ingrese el código del curso: ").strip()
            curso = next((c for c in cursos if c.codigo == codigo), None)
            if curso:
                print(f"\nCurso: {curso.nombre}")
                print(f"Estado: {curso.estado}")
                print("Alumnos:")
                for cod in curso.alumnos:
                    alumno = next((a for a in alumnos if a.codigo == cod), None)
                    if alumno:
                        print(f"  - {alumno.nombre} ({alumno.codigo})")
                print("Servidores:")
                for s in curso.servidores:
                    print(f"  - {s['nombre']}: servicios {', '.join(s['servicios_permitidos'])}")
            else:
                print("Curso no encontrado.")

        elif opcion == '3':
            codigo = input("Ingrese el código del curso: ").strip()
            curso = next((c for c in cursos if c.codigo == codigo), None)
            if not curso:
                print("Curso no encontrado.")
                continue

            print("1) Agregar")
            print("2) Eliminar")
            accion = input("Seleccione acción: ").strip()

            if accion == '1':
                cod_alumno_str = input("Ingrese el código del alumno: ").strip()
                try:
                    cod_alumno = int(cod_alumno_str)
                except ValueError:
                    print("El código debe ser un número.")
                    continue

                if cod_alumno in curso.alumnos:
                    print("El alumno ya está en el curso.")
                elif any(a.codigo == cod_alumno for a in alumnos):
                    curso.alumnos.append(cod_alumno)
                    print("Alumno agregado exitosamente.")
                else:
                    print("Alumno no registrado en el sistema.")
            elif accion == '2':
                cod_alumno_str = input("Código del alumno: ").strip()
                try:
                    cod_alumno = int(cod_alumno_str)
                except ValueError:
                    print("El código debe ser un número.")
                    continue

                if cod_alumno in curso.alumnos:
                    curso.alumnos.remove(cod_alumno)
                    print("Alumno eliminado.")
                else:
                    print("El alumno no está en este curso.")
            else:
                print("Opción inválida.")
        
        elif opcion == '0':
            break
        else:
            print("Opción inválida.")

def menu_alumnos():
    global alumnos, cursos

    while True:
        print("\n--- MENU ALUMNOS ---")
        print("1) Crear")
        print("2) Listar")
        print("3) Mostrar detalle")
        print("4) Actualizar")
        print("5) Borrar")
        print("0) Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Crear nuevo alumno ---")
            codigo_str = input("Ingrese código PUCP: ").strip()
            try:
                codigo = int(codigo_str)
            except ValueError:
                print("El código debe ser un número.")
                continue
            if any(a.codigo == codigo for a in alumnos):
                print("Ya existe un alumno con ese código.")
                continue
            nombre = input("Nombre completo: ").strip()
            mac = input("Dirección MAC (ej. 00:00:00:00:00:00): ").strip()
            nuevo = Alumno(nombre, codigo, mac)
            alumnos.append(nuevo)
            print("Alumno creado exitosamente.")

        elif opcion == '2':
            print("\n--- Lista de alumnos ---")
            for a in alumnos:
                print(f"- {a.codigo} | {a.nombre} | {a.mac}")

        elif opcion == '3':
            try:
                codigo = int(input("Ingrese el código del alumno: ").strip())
            except ValueError:
                print("Código inválido. Debe ser un número.")
                continue

            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                print(f"\nDetalles del alumno:")
                print(f"- Nombre : {alumno.nombre}")
                print(f"- Código : {alumno.codigo}")
                print(f"- MAC    : {alumno.mac}")
            else:
                print("Alumno no encontrado.")

        elif opcion == '4':
            codigo = input("Ingrese el código del alumno a actualizar: ").strip()
            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                nuevo_nombre = input(f"Nuevo nombre (enter para mantener '{alumno.nombre}'): ").strip()
                nueva_mac = input(f"Nueva MAC (enter para mantener '{alumno.mac}'): ").strip()
                if nuevo_nombre:
                    alumno.nombre = nuevo_nombre
                if nueva_mac:
                    alumno.mac = nueva_mac
                print("Alumno actualizado.")
            else:
                print("Alumno no encontrado.")

        elif opcion == '5':
            codigo = input("Ingrese el código del alumno a eliminar: ").strip()
            alumno = next((a for a in alumnos if a.codigo == codigo), None)
            if alumno:
                
                alumnos = [a for a in alumnos if a.codigo != codigo]
                # Además, eliminarlo de todos los cursos
                for c in cursos:
                    if codigo in c.alumnos:
                        c.alumnos.remove(codigo)
                print("Alumno eliminado de la lista y de todos los cursos.")
            else:
                print("Alumno no encontrado.")

        elif opcion == '0':
            break

        else:
            print("Opción inválida.")



def menu_servidores():
    global servidores

    while True:
        print("\n--- MENÚ SERVIDORES Y SERVICIOS ---")
        print("1) Listar")
        print("2) Mostrar detalles")
        print("0) Volver")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            print("\n--- Lista de servidores ---")
            for s in servidores:
                print(f"- {s.nombre} | IP: {s.ip}")

        elif opcion == '2':
            nombre = input("Ingrese el nombre del servidor(ej Servidor 1): ").strip()
            servidor = next((s for s in servidores if s.nombre.lower() == nombre.lower()), None)
            if servidor:
                print(f"\nServidor: {servidor.nombre}")
                print(f"IP: {servidor.ip}")
                print("Servicios disponibles:")
                for serv in servidor.servicios:
                    print(f"  - {serv.nombre} | Protocolo: {serv.protocolo} | Puerto: {serv.puerto}")
            else:
                print("Servidor no encontrado.")

        elif opcion == '0':
            break
        else:
            print("Opción inválida.")


def alumno_puede_conectarse(cod_alumno, servidor, servicio):
    for curso in cursos:
        if curso.estado != "DICTANDO":
            continue
        if cod_alumno not in curso.alumnos:
            continue
        for s in curso.servidores:  # <- cada s es un dict
            if s['nombre'].lower() == servidor.lower():
                if servicio.lower() in [srv.lower() for srv in s['servicios_permitidos']]:
                    return True
    print(f" El alumno {cod_alumno} no tiene acceso al servicio {servicio} en el servidor {servidor}.")
    return False


def build_arp_flow(handler, dpid, ip_src, ip_dst, out_port, sentido="arp"):
    """
    Flow para permitir ARP entre hosts.
    """
    flow = {
        "switch": dpid,
        "name": f"{handler}_{sentido}",
        "priority": "32769",  # Priorizamos ARP
        "eth_type": "0x0806",  # ARP
        "arp_spa": ip_src,  # IP de origen
        "arp_tpa": ip_dst,  # IP de destino
        "active": "true",
        "actions": f"output={out_port}"  # Acción de salida
    }
    return flow

def build_flow(handler, dpid, mac_src, ip_src, mac_dst, ip_dst, tcp_port, out_port, sentido="fw"):
    """
    Construye un flow para tráfico de L3 (IP) y L4 (TCP/UDP).
    """
    flow = {
        "switch": dpid,  # DPID del switch
        "name": f"{handler}_{sentido}",  # Flow name (handler + dirección)
        "priority": "32768",  # Prioridad del flow
        "eth_type": "0x0800",  # Tipo de Ethernet: IPv4
        "ipv4_src": ip_src,  # Dirección IP de origen
        "ipv4_dst": ip_dst,  # Dirección IP de destino
        "ip_proto": "0x06",  # Protocolo: TCP
        "tcp_dst": tcp_port,  # Puerto TCP de destino (puede cambiar según servicio)
        "active": "true",  # Flow activo
        "actions": f"output={out_port}"  # Acción: salida por el puerto
    }
    return flow


def menu_conexiones():
    while True:
        print("\n--- MENÚ CONEXIONES ---")
        print("1) Crear")
        print("2) Listar")
        print("3) Eliminar")
        print("0) Volver")
        op = input("Seleccione una opción: ").strip()

        if op == '1':
            # Pedir información del alumno, servidor y servicio
            cod_alumno_str = input("Código del alumno: ").strip()
            try:
                cod_alumno = int(cod_alumno_str)
            except ValueError:
                print("Código de alumno inválido.")
                return
            nombre_servidor = input("Nombre del servidor: ")
            nombre_servicio = input("Nombre del servicio: ")

            # Validar si el alumno tiene acceso al servicio
            if not alumno_puede_conectarse(cod_alumno, nombre_servidor, nombre_servicio):
                print(" Alumno NO autorizado para este servicio.")
                continue

            # Asignar un handler único para la conexión
            handler = str(uuid.uuid4())[:8]
            conexiones.append({'handler': handler, 'alumno': cod_alumno, 'servidor': nombre_servidor, 'servicio': nombre_servicio})
            print(f" Conexión creada. Handler: {handler}")

            # Obtener los datos necesarios para los flows
            ip_servidor = next(s.ip for s in servidores if s.nombre == nombre_servidor)
            mac_alumno = next(a.mac for a in alumnos if a.codigo == cod_alumno)

            #DPID y puerto de salida
            dpid, out_port = get_attachment_point_by_ip(ip_servidor)
            if not dpid or not out_port:
                print("Error: No se pudo obtener el DPID o puerto del servidor desde Floodlight.")
                continue

            puerto_servicio = 22 if nombre_servicio == "ssh" else 80  # Asumir puerto SSH o HTTP

            # Crear el flow de alumno a servidor (forwarding)
            flow_fw = build_flow(handler, dpid, mac_alumno, ip_servidor, mac_alumno, ip_servidor, puerto_servicio, out_port, sentido="fw")
            push_flow(flow_fw)
            print(f" Flow de Forwarding instalado: {flow_fw['name']}")

            # Crear el flow de servidor a alumno (reverse flow)
            flow_bw = build_flow(handler, dpid, mac_alumno, ip_servidor, mac_alumno, ip_servidor, puerto_servicio, 1, sentido="bw")
            push_flow(flow_bw)
            print(f" Flow de Reverse instalado: {flow_bw['name']}")

            # Flujos ARP (para resolución de IPs)
            flow_arp_fw = build_arp_flow(handler, dpid, ip_servidor, ip_servidor, out_port, sentido="arp_fw")
            push_flow(flow_arp_fw)
            print(f" Flow ARP Forward instalado: {flow_arp_fw['name']}")

            flow_arp_bw = build_arp_flow(handler, dpid, ip_servidor, ip_servidor, 1, sentido="arp_bw")
            push_flow(flow_arp_bw)
            print(f" Flow ARP Reverse instalado: {flow_arp_bw['name']}")

        elif op == '2':
            if not conexiones:
                print("No hay conexiones creadas.")
            else:
                for c in conexiones:
                    print(f"Handler: {c['handler']}, Alumno: {c['alumno']}, Servidor: {c['servidor']}, Servicio: {c['servicio']}")
        elif op == '3':
            handler = input("Handler de la conexión a eliminar: ")
            for i, c in enumerate(conexiones):
                if c['handler'] == handler:
                    # Eliminar los flows correspondientes en Floodlight
                    delete_flow(f"{handler}_fw")
                    delete_flow(f"{handler}_bw")
                    delete_flow(f"{handler}_arp_fw")
                    delete_flow(f"{handler}_arp_bw")

                    # Eliminar la conexión de la lista
                    conexiones.pop(i)
                    print(" Conexión eliminada y flows removidos.")
                    break
            else:
                print(" No se encontró el handler.")
        elif op == '0':
            break
        else:
            print(" Opción inválida.")

def get_attachment_point_by_ip(ip):
    url = f"{BASE_URL}/wm/device/"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            for dev in r.json():
                if ip in dev.get("ipv4", []):
                    ap = dev.get("attachmentPoint", [])
                    if ap:
                        return ap[0].get("switchDPID"), ap[0].get("port")
    except Exception as e:
        print(f"Error al consultar Floodlight: {e}")
    return None, None


def push_flow(flow):
    url = f"{BASE_URL}/wm/staticflowpusher/json"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=flow, headers=headers)
        if response.status_code == 200:
            print(" Flow instalado en Floodlight.")
        else:
            print(f" Error al instalar flow: {response.text}")
    except Exception as e:
        print(f" No se pudo conectar a Floodlight: {e}")


def delete_flow(flow_name):
    url = f"{BASE_URL}/wm/staticflowpusher/json"
    data = {"name": flow_name}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.delete(url, json=data, headers=headers)
        if response.status_code == 200:
            print(" Flow eliminado de Floodlight.")
        else:
            print(f" Error al eliminar flow: {response.text}")
    except Exception as e:
        print(f" No se pudo conectar a Floodlight: {e}")


def mostrar_menu():
    print("####################################################")
    print("Network Policy manager de la UPSM")
    print("####################################################")
    print("1. Importar")
    print("2. Exportar")
    print("3. Cursos")
    print("4. Alumnos")
    print("5. Servidores")
    print("6. Politicas")
    print("7. Conexiones")
    print("8. Salir")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            archivo = input("Nombre de archivo a importar: ")
            importar_yaml(archivo)
            print(f"Archivo {archivo} importado exitosamente")
        elif opcion == '2':
            archivo = input("Ingrese el nombre del archivo para exportar: ")
            exportar_yaml(archivo, alumnos, cursos, servidores)
            print(f"Archivo {archivo} exportado correctamente.")
        elif opcion == '3':
            menu_cursos()
        elif opcion == '4':
            menu_alumnos()
        elif opcion == '5':
            menu_servidores()
        elif opcion == '6':
            break
        elif opcion == '7':
            menu_conexiones()
        elif opcion == '8':
            print("Cerrando programa.")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
