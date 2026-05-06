def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def parse_resources(rs):
        out = []
        for r in rs or []:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((r[0], r[1]))
            elif isinstance(r, dict):
                pos = r.get("position") or r.get("pos") or r.get("location")
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    out.append((pos[0], pos[1]))
        return out

    resources = parse_resources(observation.get("resources"))
    targets = [t for t in resources if inb(t[0], t[1]) and t not in obs]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if targets:
        tx, ty = min(targets, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        best = None
        bestd = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(tx - nx) + abs(ty - ny)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        best = None
        bestd = -1
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd:
                bestd = d
                best = [dx, dy]
        return best if best is not None else [0, 0]