def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    ox1 = abs(ox - sx) + abs(oy - sy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_to_opp = abs(ox - nx) + abs(oy - ny)
        v = 0
        if resources:
            dmin = min(abs(rx - nx) + abs(ry - ny) for (rx, ry) in resources)
            v += -dmin * 10
            if any(nx == rx and ny == ry for (rx, ry) in resources):
                v += 500
        if d_to_opp <= 1:
            v -= 200
        else:
            if ox1 > 0:
                v += (d_to_opp - ox1) * 2
        if best is None or v > bestv:
            bestv = v
            best = [dx, dy]

    if best is not None:
        return best
    return [0, 0]