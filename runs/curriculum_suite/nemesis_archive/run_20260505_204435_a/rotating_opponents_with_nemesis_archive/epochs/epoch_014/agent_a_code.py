def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    targets = []
    for r in resources:
        if isinstance(r, dict):
            if "position" in r and isinstance(r["position"], (list, tuple)) and len(r["position"]) >= 2:
                targets.append((r["position"][0], r["position"][1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    if not targets:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            sc = man(nx, ny, ox, oy)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    tx, ty = min(targets, key=lambda t: man(sx, sy, t[0], t[1]))
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        d_opp_now = man(sx, sy, ox, oy)
        sc = -d_self + 0.2 * d_opp
        if d_self < man(sx, sy, tx, ty): sc += 0.5
        if d_opp > d_opp_now: sc += 0.1
        if best is None or sc > best[0]:
            best = (sc, dx, dy)
    return [best[1], best[2]] if best else [0, 0]