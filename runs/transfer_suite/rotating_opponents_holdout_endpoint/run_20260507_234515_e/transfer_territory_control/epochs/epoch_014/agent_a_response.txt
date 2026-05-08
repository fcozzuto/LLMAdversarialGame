def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    def to_cells(lst):
        out = []
        for p in (lst or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                out.append((int(p[0]), int(p[1])))
        return out

    obstacles = set(to_cells(observation.get("obstacles", []) or []))
    unclaimed = set(to_cells(observation.get("unclaimed_cells", []) or []))
    self_terr = set(to_cells(observation.get("self_territory", []) or []))
    opp_terr = set(to_cells(observation.get("opponent_territory", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if unclaimed:
        target = min(unclaimed, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
    else:
        all_cells = self_terr | opp_terr
        if all_cells:
            target = min(all_cells, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), p[0], p[1]))
        else:
            target = (sx, sy)

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        np = (nx, ny)

        if np in unclaimed:
            val = 3.0
        elif np in opp_terr:
            val = 1.6  # flipping expected on entry
        elif np in self_terr:
            val = 0.3
        else:
            val = 0.1

        d = abs(nx - target[0]) + abs(ny - target[1])
        val += -0.12 * d

        # Frontier bias: prefer cells adjacent to our territory to expand coherently
        neigh = 0
        for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + adx, ny + ady
            if inside(ax, ay) and (ax, ay) in self_terr:
                neigh += 1
        val += 0.15 * neigh

        # Deterministic tie-break via move order
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]