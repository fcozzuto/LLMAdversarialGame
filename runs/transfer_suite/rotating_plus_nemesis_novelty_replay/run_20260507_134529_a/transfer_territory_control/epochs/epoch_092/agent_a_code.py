def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

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
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            # Base preference to expand/flip.
            if (nx, ny) in opp_terr:
                val = 10.0
            elif (nx, ny) in unclaimed:
                val = 4.5
            elif (nx, ny) in self_terr:
                val = 1.0
            else:
                val = 2.0
            # Resource bump.
            if (nx, ny) in resources:
                val += 6.0
            # Push toward opponent and away from edges we can be cut by.
            dist_opp = abs(nx - ox) + abs(ny - oy)
            val += 0.25 * (16 - dist_opp)
            # Prefer progressing from our current position (reduce dithering).
            val += 0.1 * (abs(nx - sx) + abs(ny - sy))
            # Slight deterministic nudge to break ties.
            val += 0.0001 * ((nx + 3 * ny + int(observation.get("turn_index", 0))) % 7)
            cand.append((val, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]