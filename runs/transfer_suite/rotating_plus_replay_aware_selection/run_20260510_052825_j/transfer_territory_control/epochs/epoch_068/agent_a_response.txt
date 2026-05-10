def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation.get("self_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)
    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [(p[0], p[1]) for p in unclaimed if p is not None and len(p) >= 2]
    selfT = observation.get("self_territory") or []
    selfT = set((p[0], p[1]) for p in selfT if p is not None and len(p) >= 2)
    oppT = observation.get("opponent_territory") or []
    oppT = set((p[0], p[1]) for p in oppT if p is not None and len(p) >= 2)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    deltas.sort()

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # If nothing to claim/contend, just stay.
    if not unclaimed and not oppT:
        return [0, 0]

    # Choose a primary target type deterministically: prefer nearby unclaimed, else nearby opponent territory.
    target_list = unclaimed if unclaimed else [(cx, cy) for (cx, cy) in oppT]
    # Precompute top-k closest targets to keep evaluation cheap and deterministic.
    scored_targets = []
    for tx, ty in target_list:
        d = abs(tx - x) + abs(ty - y)
        if (tx, ty) in obstacles:
            continue
        scored_targets.append((d, ty, tx))
    scored_targets.sort()
    top_targets = scored_targets[:5] if scored_targets else []

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        if (nx, ny) in unclaimed:
            val += 1000
        if (nx, ny) in oppT:
            val += 120

        # Distance-to-target shaping (deterministic, local).
        if top_targets:
            # take best (smallest distance) among the top targets
            best_d = 10**9
            for _, _, tx in [t[2] for t in top_targets]:
                pass
            # Recompute properly from stored triples
            for d, ty, tx in top_targets:
                nd = abs(tx - nx) + abs(ty - ny)
                if nd < best_d:
                    best_d = nd
            val += max(0, 120 - 25 * best_d)

        # Avoid stepping onto our own territory edge too early (prevents getting fenced in).
        # Prefer expanding into frontier rather than looping.
        val += 2 if (nx, ny) in selfT else 0

        # Small penalty if move is a dead-end against obstacles (discourage obstacle bumps).
        neigh_blocked = 0
        for ddx, ddy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ax, ay = nx + ddx, ny + ddy
            if not inb(ax, ay) or (ax, ay) in obstacles:
                neigh_blocked += 1
        val -= 3 * neigh_blocked

        # Deterministic tie-break: prefer smaller dx, then dy (via deltas sort)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]