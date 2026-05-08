def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
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
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (float("-inf"), 0, 0)

    def cell_value(nx, ny):
        if (nx, ny) in obstacles:
            return float("-inf")
        if (nx, ny) in opp_terr:
            base = 7.0
        elif (nx, ny) in unclaimed:
            base = 3.2
        elif (nx, ny) in self_terr:
            base = 1.0
        else:
            base = 0.8
        if (nx, ny) in resources:
            base += 2.0
        # Prefer center pressure but also punish moving toward opponent too closely.
        d_center = abs(nx - cx) + abs(ny - cy)
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Normalize by grid size to keep stable across maps.
        return base + 0.35 * (16.0 - d_center) - 0.18 * d_opp

    # Deterministic tie-break: prefer moves with larger dx, then larger dy.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            v = cell_value(nx, ny)
        else:
            nx, ny = sx, sy
            v = cell_value(nx, ny)
        if v > best[0] or (v == best[0] and (dx, dy) > (best[1], best[2])):
            best = (v, dx, dy)

    return [int(best[1]), int(best[2])]