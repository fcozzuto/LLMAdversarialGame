def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obstacle_density(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0)
    best_val = -10**18

    # Strategy change: minimize opponent's ability to reach a contested target by maximizing
    # (my advantage - closeness to opponent), with secondary bias to safer/denser-gradient positions.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Avoid walking into opponent unless it also improves resource contention.
        opp_close = king_dist(nx, ny, ox, oy)
        avoid = (3.5 - opp_close)  # positive if close (bad), negative if far (good)

        val = 0.0
        if resources:
            # Choose a target that best improves our relative arrival vs opponent.
            # Use multiple candidates to avoid getting stuck on a resource the opponent can take.
            best_contest = -10**18
            for rx, ry in resources:
                my_t = king_dist(nx, ny, rx, ry)
                op_t = king_dist(ox, oy, rx, ry)
                # Positive means we are faster; strongly prefer targets where we can be faster.
                contest = (op_t - my_t)
                # Also slightly prefer nearer targets for both.
                contest -= 0.2 * my_t
                best_contest = contest if contest > best_contest else best_contest
            val += 4.0 * best_contest
        # Safety/flow: prefer positions with fewer nearby obstacles when not currently winning contests.
        val -= 0.15 * obstacle_density(nx, ny)
        # Strongly discourage moving adjacent to opponent when no resource contest exists.
        if not resources or (resources and val < 1.0):
            val -= 2.0 * avoid

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still.
        tie = (val == best_val)
        if val > best_val or (tie and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]