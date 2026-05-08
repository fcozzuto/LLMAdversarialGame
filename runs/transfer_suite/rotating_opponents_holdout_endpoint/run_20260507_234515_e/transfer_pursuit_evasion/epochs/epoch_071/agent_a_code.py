def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oset

    resources = observation.get("resources", None)
    targets = []
    if isinstance(resources, (list, tuple)):
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                tx, ty = int(r[0]), int(r[1])
                if 0 <= tx < w and 0 <= ty < h:
                    targets.append((tx, ty))
            elif isinstance(r, dict):
                if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                    tx, ty = int(r["position"][0]), int(r["position"][1])
                else:
                    tx, ty = int(r.get("x", -1) or -1), int(r.get("y", -1) or -1)
                if 0 <= tx < w and 0 <= ty < h:
                    targets.append((tx, ty))

    role = (observation.get("self_role", "") or "").lower()
    evader = ("evad" in role) and ("purs" not in role)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if targets:
            dmin = None
            for tx, ty in targets:
                d = abs(nx - tx) + abs(ny - ty)
                if dmin is None or d < dmin:
                    dmin = d
            key = (dmin, abs(nx - ox) + abs(ny - oy))
            if evader:
                key = (-key[0], -key[1])
        else:
            dopp = abs(nx - ox) + abs(ny - oy)
            key = (dopp, nx, ny)
            if evader:
                key = (-dopp, nx, ny)

        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]