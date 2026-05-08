def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    un = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    my = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))

    ox, oy = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(ox), int(oy)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        if (nx, ny) in my:
            base = 0
        elif (nx, ny) in un:
            base = 3
        elif (nx, ny) in opp:
            base = 6
        else:
            base = 1

        # Prefer cells that reduce distance to the nearest frontier
        best_d = 10**9
        if un:
            for ux, uy in un:
                d = abs(ux - nx) + abs(uy - ny)
                if d < best_d:
                    best_d = d
        elif opp:
            for px, py in opp:
                d = abs(px - nx) + abs(py - ny)
                if d < best_d:
                    best_d = d
        else:
            best_d = abs(ox - nx) + abs(oy - ny)

        # Encourage disruption near opponent
        disrupt = - (abs(ox - nx) + abs(oy - ny)) / 10.0

        return base * 1000 - best_d * 10 + disrupt

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = cell_score(nx, ny)
        # Tie-break deterministically by move
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]