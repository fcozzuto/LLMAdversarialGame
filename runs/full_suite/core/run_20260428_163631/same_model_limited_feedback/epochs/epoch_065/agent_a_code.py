def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx*dx + dy*dy

    # If no resources, drift toward center deterministically
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -10**9)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            score = -d2(nx, ny, tx, ty)
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_score = -10**18

    # Choose a target resource biased against opponent closer access
    def target_eval(nx, ny, rx, ry):
        # Encourage moving toward resources; penalize giving opponent closer turns.
        my = d2(nx, ny, rx, ry)
        op = d2(ox, oy, rx, ry)
        # If we can reach quickly, prioritize. If opponent is closer, reduce priority.
        return -my + 0.35 * op

    # Precompute best resource scores from candidate positions
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        # If we step onto a resource, strong reward
        here_res = 1
        for rx, ry in resources:
            if rx == nx and ry == ny:
                here_res = 10
                break

        # Best target reachable after the move
        best_t = -10**18
        for rx, ry in resources:
            if (rx == nx and ry == ny):
                score_t = 10**9
            else:
                score_t = target_eval(nx, ny, rx, ry)
            if score_t > best_t:
                best_t = score_t

        # Slight preference for staying closer to opponent (interference) if neutral
        interference = -0.02 * d2(nx, ny, ox, oy)
        total = here_res + best_t + interference

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]