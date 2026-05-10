def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist_to_center(x, y):
        dx = x - cx
        dy = y - cy
        return dx * dx + dy * dy

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_dxdy = (0, 0)
    best_val = -10**18

    # Mild bias to continue toward the densest nearby frontier: unclaimed preferred; then opponent territory.
    # Also prefer moves that reduce distance to the opponent (more chances to flip).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 420
        if (nx, ny) in opp_terr:
            val += 160  # flipping on entry
        if (nx, ny) in self_terr:
            val += 12

        # Frontier/pressure: pick moves that move closer to the opponent while staying in safe region.
        cur_dop = manh(sx, sy, px, py)
        new_dop = manh(nx, ny, px, py)
        val += (cur_dop - new_dop) * 6

        # Keep spreading toward the center to avoid cornering too early.
        val += (dist_to_center(sx, sy) - dist_to_center(nx, ny)) * 1.5

        # If this cell is adjacent to opponent territory, boost (likely to secure more on next turns).
        adj = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in opp_terr:
                adj += 1
        val += adj * 18

        # If we're moving away from any nearby unclaimed frontier, penalize slightly.
        # (Compute nearest unclaimed distance from the candidate cell within a small radius.)
        nearest = 10**9
        if unclaimed:
            r = 3
            x0, y0 = nx - r, ny - r
            x1, y1 = nx + r, ny + r
            for ux, uy in unclaimed:
                if x0 <= ux <= x1 and y0 <= uy <= y1:
                    d = abs(ux - nx) + abs(uy - ny)
                    if d < nearest:
                        nearest = d
        if nearest != 10**9:
            val += max(0, (4 - nearest)) * 10

        # Deterministic tie-break: prefer staying if equal, else lexicographic dx,dy order.
        if val > best_val:
            best_val = val
            best_dxdy = (dx, dy)
        elif val == best_val:
            if (dx, dy) == (0, 0) and best_dxdy != (0, 0):
                best_dxdy = (dx, dy)
            elif best_dxdy != (0, 0) and (dx, dy) != (0, 0):
                if (dx, dy) < best_dxdy:
                    best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]