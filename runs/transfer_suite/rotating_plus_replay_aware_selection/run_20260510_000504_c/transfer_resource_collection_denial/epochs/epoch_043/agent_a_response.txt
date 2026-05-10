def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            if "position" in p and isinstance(p["position"], (list, tuple)) and len(p["position"]) >= 2:
                obstacles.add((int(p["position"][0]), int(p["position"][1])))
            else:
                if "x" in p and "y" in p:
                    obstacles.add((int(p["x"]), int(p["y"])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                resources.append((int(r["position"][0]), int(r["position"][1])))
            else:
                if "x" in r and "y" in r:
                    resources.append((int(r["x"]), int(r["y"])))

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in resources:
        sd = max(abs(tx - sx), abs(ty - sy))
        od = max(abs(tx - ox), abs(ty - oy))
        # Prefer resources where we arrive earlier; then closer; then deterministic tie-break by coordinates.
        key = (od - sd, -sd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    desired = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = max(abs(tx - nx), abs(ty - ny))
        # Prefer reducing distance; slight bias to diagonals when equally good.
        diag_bias = 1 if dx != 0 and dy != 0 else 0
        desired.append((nd, -diag_bias, dx, dy))
    if not desired:
        return [0, 0]

    desired.sort()
    _, _, dx, dy = desired[0]
    return [int(dx), int(dy)]