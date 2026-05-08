def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)

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

    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def neighbor_count(cellset, x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in cellset:
                c += 1
        return c

    best = (float("-inf"), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue

        if (nx, ny) in opp_terr:
            base = 8.0
        elif (nx, ny) in unclaimed:
            base = 3.6
        elif (nx, ny) in self_terr:
            base = 0.6
        else:
            base = 0.25

        if (nx, ny) in resources:
            base += 2.8

        # Prefer moves that strengthen your local frontier; lightly discourage giving opponent proximity.
        frontier = 0.25 * (neighbor_count(unclaimed, nx, ny) + 0.6 * neighbor_count(self_terr, nx, ny))
        contest = 0.12 * (manh(nx, ny, ox, oy) == 0)  # rare, but deterministic
        chase = -0.04 * manh(nx, ny, ox, oy)

        # If you're surrounded, stay or pick best among available.
        score = base + frontier + contest + chase

        if score > best[0] or (score == best[0] and (dx, dy) == (0, 0)):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]