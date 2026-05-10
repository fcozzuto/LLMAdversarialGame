def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-breaking: fixed move order; only compute scalar scores.
    def dist2(x, y):
        return (x - ax) * (x - ax) + (y - ay) * (y - ay)

    # Find a target that best supports expansion; prefer unclaimed.
    candidates = []
    if un_set:
        # Sample a few closest unclaimed deterministically.
        items = sorted(un_set, key=lambda p: dist2(p[0], p[1]))[:18]
        candidates = items
    else:
        candidates = sorted(op_set, key=lambda p: dist2(p[0], p[1]))[:18] if op_set else []

    # Also consider "frontier" cells: unclaimed adjacent to opponent territory.
    frontier = []
    if un_set and op_set:
        for (x, y) in un_set:
            # cheap adjacency check
            if (x - 1, y) in op_set or (x + 1, y) in op_set or (x, y - 1) in op_set or (x, y + 1) in op_set:
                frontier.append((x, y))
        if frontier:
            frontier = sorted(frontier, key=lambda p: dist2(p[0], p[1]))[:12]
            candidates = frontier + candidates[:6]

    if candidates:
        tx, ty = min(candidates, key=lambda p: (dist2(p[0], p[1]), abs(p[0] - (w - 1) / 2) + abs(p[1] - (h - 1) / 2)))
    else:
        tx, ty = int((w - 1) / 2), int((h - 1) / 2)

    # Heuristic scoring for next cell.
    # Prefer: unclaimed (big), capture opponent (medium), reduce distance to target.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        val = 0
        if (nx, ny) in un_set:
            val += 120
        elif (nx, ny) in op_set:
            val += 70
        elif (nx, ny) in my_set:
            val += 10
        # Gain by moving closer to target
        val += 30 - 2 * dist2(nx, ny)
        # Slight preference to approach enemy frontiers if close
        if op_set:
            dmin = None
            # check local neighborhood only (fast, deterministic)
            for ox, oy in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)]:
                if (ox, oy) in op_set:
                    dmin = 0
                    break
            if dmin == 0:
                val += 25
        # Discourage walking into "likely opponent capture" by moving directly onto their territory without also being near unclaimed
        if (nx, ny) in op_set:
            # If adjacent unclaimed exists, keep; else reduce.
            adj_un = ((nx-1, ny) in un_set) or ((nx+1, ny) in un_set) or ((nx, ny-1) in un_set) or ((nx, ny+1) in un_set)
            if not adj_un:
                val -= 10
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move