def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    pursuit = ("purs" in self_role) or ("purs" in opponent_role and "evad" not in self_role)

    resources = observation.get("resources", []) or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_list.append((rx, ry))
    aim_resource = len(res_list) > 0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = [0, 0]
    best_sc = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        manh = abs(nx - ox) + abs(ny - oy)
        if pursuit and (nx == ox and ny == oy):
            return [dx, dy]
        if (not pursuit) and (nx == ox and ny == oy):
            # Avoid immediate capture when evading
            sc = -10**9
        else:
            sc = 0.0
            # Main objective: chase or run
            sc += (-manh if pursuit else manh) * 1000.0

            # Secondary objective: move toward nearest resource only if it helps
            if aim_resource:
                dmin = None
                for rx, ry in res_list:
                    d = abs(nx - rx) + abs(ny - ry)
                    if dmin is None or d < dmin:
                        dmin = d
                if dmin is not None:
                    sc += (-dmin if not pursuit else dmin * 0.2)

            # Tertiary objective: prefer staying away from obstacles "edges" slightly
            # (deterministic and cheap)
            neigh_blocked = 0
            for ddx, ddy in deltas:
                tx, ty = nx + ddx, ny + ddy
                if 0 <= tx < w and 0 <= ty < h and (tx, ty) in blocked:
                    neigh_blocked += 1
            sc += (-neigh_blocked if pursuit else neigh_blocked) * 1.0

        if best_sc is None or (sc > best_sc if not pursuit else sc > best_sc):
            best_sc = sc
            best_move = [dx, dy]

    return best_move