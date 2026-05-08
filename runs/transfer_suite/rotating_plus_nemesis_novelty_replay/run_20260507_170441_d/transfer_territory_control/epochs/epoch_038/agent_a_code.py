def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = observation.get("resources") or []
    res_cells = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res_cells.append((x, y))
        except:
            pass

    leading = float((observation.get("scores") or {}).get(observation.get("self_name", "agent_a"), 0.0) or 0.0)
    scores = observation.get("scores") or {}
    my_name = observation.get("self_name", "agent_a")
    opp_name = observation.get("opponent_name", "agent_b")
    my_score = float(scores.get(my_name, scores.get("agent_a", 0.0)) or 0.0)
    opp_score = float(scores.get(opp_name, scores.get("agent_b", 0.0)) or 0.0)

    best = None
    bestv = None

    if res_cells:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            md = None
            for rx, ry in res_cells:
                d = abs(nx - rx) + abs(ny - ry)
                if md is None or d < md:
                    md = d
            if md is None:
                continue
            od = abs(ox - min(res_cells, key=lambda p: abs(nx - p[0]) + abs(ny - p[1]))[0]) + abs(oy - min(res_cells, key=lambda p: abs(nx - p[0]) + abs(ny - p[1]))[1])
            v = md * (2 if not (my_score > opp_score) else 1) + (0 if my_score > opp_score else od / 10.0)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
    else:
        tx, ty = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dcenter = abs(nx - tx) + abs(ny - ty)
            dopp = abs(nx - ox) + abs(ny - oy)
            v = dcenter + (-0.5 if my_score > opp_score else -1.0) * min(dopp, 3)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best[0]), int(best[1])]