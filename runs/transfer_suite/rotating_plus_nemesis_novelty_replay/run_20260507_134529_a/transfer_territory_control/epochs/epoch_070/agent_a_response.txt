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

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Frontier: unclaimed cells adjacent to opponent territory.
    frontier = set()
    for (px, py) in opp_terr:
        for dx, dy in neigh8:
            nx, ny = px + dx, py + dy
            if (nx, ny) in unclaimed:
                frontier.add((nx, ny))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cand = []
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        base = 0.0
        if (nx, ny) in opp_terr:
            base = 10.0
        elif (nx, ny) in frontier:
            base = 6.5
        elif (nx, ny) in unclaimed:
            base = 3.2
        elif (nx, ny) in self_terr:
            base = 1.0
        else:
            base = 0.6
        if (nx, ny) in resources:
            base += 2.0

        # Prefer moving toward opponent territory; slight preference to be closer.
        if opp_terr:
            dist_to_opp = min(manh(nx, ny, tx, ty) for (tx, ty) in opp_terr)
            base += max(0.0, 4.0 - 0.35 * dist_to_opp)
        # Also avoid drifting into the opponent's current position too much.
        base += -0.03 * man(nx, ny, ox, oy)

        cand.append((base, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]