def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, w - 1, h - 1

    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursur" in role) or (role == "pursuer") or ("pursuer" in role)

    resources = observation.get("resources", []) or []
    rem_cnt = observation.get("remaining_resource_count", 0)
    prefer_resource = bool(rem_cnt) and bool(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step(dx, dy):
        nx, ny = sx + dx, sy + dy
        return (nx, ny) if inb(nx, ny) else (sx, sy)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = cand[0]
    bestv = -10**18 if pursuer else 10**18

    nearest_res = None
    if prefer_resource:
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = r[0], r[1]
                try:
                    rx, ry = int(rx), int(ry)
                except:
                    continue
                d = man(sx, sy, rx, ry)
                if nearest_res is None or d < nearest_res[0]:
                    nearest_res = (d, rx, ry)

    for dx, dy in cand:
        nx, ny = step(dx, dy)
        d_opp = man(nx, ny, ox, oy)
        if prefer_resource and nearest_res is not None:
            _, rx, ry = nearest_res
            d_res = man(nx, ny, rx, ry)
        else:
            d_res = 0

        v = -d_opp
        if not pursuer:
            v = d_opp
        if prefer_resource and nearest_res is not None:
            v += (-d_res if pursuer else -d_res) * 0.01

        if (pursuer and v > bestv) or ((not pursuer) and v < bestv):
            bestv, best = v, (dx, dy)

    dx, dy = best
    return [dx, dy]