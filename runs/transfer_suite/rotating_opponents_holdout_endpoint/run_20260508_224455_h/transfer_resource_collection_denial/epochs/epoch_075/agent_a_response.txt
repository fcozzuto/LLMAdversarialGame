def choose_move(observation):
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    gw, gh = int(observation["grid_width"]), int(observation["grid_height"])
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Precompute resource positions as ints for determinism/clarity
    res = [(int(r[0]), int(r[1])) for r in resources]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: maximize how much closer we are than opponent to any resource
        # Secondary: among those, minimize our distance to that resource
        # Tertiary: nudge toward resources that are "contested" (small lead for opponent to steal)
        best_margin = -10**18
        best_myd = 10**18
        best_contest = 10**18
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd
            if margin > best_margin or (margin == best_margin and myd < best_myd):
                best_margin, best_myd = margin, myd

        # Contest metric for that best target: prefer positions that force quick win
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd - myd == best_margin and myd == best_myd:
                # If opponent is also close, being slightly better matters more
                best_contest = abs(opd - myd)
                break

        # If we can step onto a resource immediately, that's very strong
        immediate = 1 if (nx, ny) in obstacles else 0
        # immediate resource check
        is_resource_here = 0
        for rx, ry in res:
            if rx == nx and ry == ny:
                is_resource_here = 1
                break

        # Value: large reward for immediate pick, then lead over opponent
        # Slight penalty for staying away; slight penalty for moves that don't improve relative lead
        val = 0
        if is_resource_here:
            val += 10**9
        val += best_margin * 1000
        val += -best_myd
        val += -best_contest * 2
        # Small preference to move (unless equally good) to avoid being farmed by row sweeps
        if (dx, dy) != (0, 0):
            val += 3

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]