def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = [tuple(xy) for xy in (observation.get("unclaimed_cells", []) or [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    ox, oy = (observation.get("opponent_position", [w - 1, h - 1]) + [w - 1, h - 1])[:2]

    # Precompute a small set of relevant unclaimed targets (nearby first)
    u_sorted = sorted(unclaimed, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    u_top = u_sorted[:20] if u_sorted else []

    def min_dist_to_unclaimed(x, y):
        if not u_top:
            return 0
        best = 10**9
        for tx, ty in u_top:
            d = abs(tx - x) + abs(ty - y)
            if d < best:
                best = d
        return best if best != 10**9 else 0

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            # invalid moves rejected by staying; still consider as staying cell with same heuristic
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell_val = 0
        if (nx, ny) in self_cells:
            cell_val = 1
        elif (nx, ny) in opp_cells:
            cell_val = 6  # flipping opponent territory on entry
        elif (nx, ny) not in obstacles:
            cell_val = 3  # unclaimed or other claimable
        # Aim for nearby unclaimed; also keep some pressure by moving towards opponent slightly
        d_un = min_dist_to_unclaimed(nx, ny)
        d_op = abs(nx - ox) + abs(ny - oy)
        val = cell_val * 100 - d_un * 3 + (-d_op) * 0.6
        # Encourage expansion from our boundary: moving to a cell adjacent to unclaimed
        if unclaimed:
            for tx, ty in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
                if (tx, ty) in unclaimed:
                    val += 8
                    break
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]