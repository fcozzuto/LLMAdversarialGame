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
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer capturing near opponent frontier; otherwise counterclaim.
    frontier = set()
    for (x, y) in opp_terr:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                    frontier.add((nx, ny))

    target_set = frontier if frontier else (opp_terr if opp_terr else unclaimed)

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place if invalid
        val = 0.0
        if (nx, ny) in opp_terr:
            val += 7.5
        elif (nx, ny) in unclaimed:
            val += 3.8
        elif (nx, ny) in self_terr:
            val += 1.2
        else:
            val += 0.6
        if (nx, ny) in resources:
            val += 2.3

        # Pressure opponent (move closer to where counterclaim likely matters).
        d_before = dist((sx, sy), (ox, oy))
        d_after = dist((nx, ny), (ox, oy))
        val += 0.65 * (d_before - d_after)

        # Aim for nearest target cell from frontier/unclaimed/opp terr.
        if target_set:
            best_t = None
            best_td = 10**9
            for (tx, ty) in target_set:
                td = abs(tx - nx) + abs(ty - ny)
                if td < best_td:
                    best_td = td
                    best_t = (tx, ty)
            val += 0.35 * (best_td * -1 if best_t is not None else 0)

        # Small penalty for stepping back-and-forth (prefer deterministic "progress" via dx/dy order).
        if dx == 0 and dy == 0:
            val -= 0.15

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]