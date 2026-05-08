def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (0, 0)
    best_sc = -10**18

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = 0
        if resources:
            # Prefer closer to nearest resource.
            sc += -min(man(nx, ny, rx, ry) for (rx, ry) in resources) * 10
            if (nx, ny) in resources:
                sc += 2000
        else:
            # No explicit resources: drift toward center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            sc += -(abs(nx - cx) + abs(ny - cy)) * 0.5

        # Stay away from opponent.
        sc += man(nx, ny, ox, oy) * 6
        if (nx, ny) in opp_terr:
            sc -= 500
        if (nx, ny) in self_terr:
            sc += 15

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]