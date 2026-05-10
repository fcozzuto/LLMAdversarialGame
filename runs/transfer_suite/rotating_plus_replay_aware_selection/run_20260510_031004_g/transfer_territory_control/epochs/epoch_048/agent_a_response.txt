def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    px, py = observation.get("opponent_position", [0, 0])

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Heuristics: prioritize (1) capturing unclaimed, (2) stepping into opponent territory to flip,
    # (3) extending toward unclaimed that lie on/near opponent territory edges,
    # (4) reducing distance to opponent, while (5) avoiding giving up immediate capture.
    best = (0, 0)
    best_val = -10**18

    def edge_score(x, y):
        if (x, y) not in unclaimed:
            return 0
        # Encourage unclaimed cells adjacent to opponent territory (likely frontier expansion).
        s = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in opp_terr:
                    s += 1
        return 40 * s

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        val = 0

        # Immediate capture value
        if (nx, ny) in unclaimed:
            val += 320 + edge_score(nx, ny)
            # Prefer capturing unclaimed closer to opponent (frontline pressure)
            val += 3 * (max(abs(nx - px), abs(ny - py)) * -1)
        if (nx, ny) in opp_terr:
            val += 140  # flipping on entry
            # Prefer flipping closer to where opponent is
            val += 8 * (max(abs(sx - px), abs(sy - py)) - max(abs(nx - px), abs(ny - py)))

        if (nx, ny) in self_terr:
            val += 15  # keep territory contiguous

        # Distance pressure (Voronoi-like)
        d_self = max(abs(nx - px), abs(ny - py))
        d_oppo = max(abs(px - nx), abs(py - ny))  # same as d_self, but keep symmetry in heuristic
        val += 0  # no-op; deterministic placeholder removed

        # Reduce distance to opponent generally
        val += 6 * (max(abs(sx - px), abs(sy - py)) - max(abs(nx - px), abs(ny - py)))

        # Slight preference to avoid stagnation if already have moves to capture
        if dx == 0 and dy == 0:
            val -= 25

        # Tie-break deterministically by dir order and then value
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]