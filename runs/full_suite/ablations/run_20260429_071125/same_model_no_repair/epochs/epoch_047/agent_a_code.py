def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Heuristic: For each move, pick the resource that gives best "capture pressure"
    # Value uses (opponent_dist - our_dist), plus strong bonuses for near/instant capture,
    # and penalties when opponent is strictly closer.
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_val = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            du = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)

            # Capture priority
            val = (do - du) * 1000

            # Big bonus for capturing now, smaller for capturing next
            if du == 0:
                val += 10**7
            elif du == 1:
                val += 10**5

            # If opponent can reach earlier, heavily penalize
            if do < du:
                val -= (du - do) * 10**6
            elif do == du:
                val -= 20000  # contested; prefer moves with advantage

            # Light tie-break to reduce wasted motion: prefer being closer overall
            val -= du * 25

            if val > move_val:
                move_val = val

        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move