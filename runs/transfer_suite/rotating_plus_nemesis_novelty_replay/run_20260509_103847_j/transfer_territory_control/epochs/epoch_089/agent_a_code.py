def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine will keep us in place
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        adj_op = 0
        adj_un = 0
        adj_self = 0
        for ax, ay in adj8(nx, ny):
            if (ax, ay) in opT:
                adj_op += 1
            if (ax, ay) in unT:
                adj_un += 1
            if (ax, ay) in selfT:
                adj_self += 1

        on_op = 1 if (nx, ny) in opT else 0
        on_self = 1 if (nx, ny) in selfT else 0
        on_un = 1 if (nx, ny) in unT else 0

        # If we can flip opponent territory on entry, prioritize strongly.
        # Otherwise, expand into unclaimed and keep a coherent frontier.
        dist_to_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        dist_from_opp = abs(nx - ox) + abs(ny - oy)

        v = 0
        v += on_op * 35
        v += adj_op * 6
        v += on_un * 10
        v += adj_un * 2
        v += on_self * 1
        v += adj_self * 0.5
        v += dist_from_opp * 0.15  # prefer creating distance while taking borders
        v -= dist_to_center * 0.03  # mild center preference

        # Tie-break deterministically: prefer not staying still unless it's clearly best
        v -= (0 if (dx != 0 or dy != 0) else 0.25)

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return [int(best[0]), int(best[1])]