def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    # Deterministic mode shift to avoid repeating same policy: odd/even turn changes preference
    odd_mode = (int(observation.get("turn_index", 0) or 0) % 2) == 1
    eps = 1 if odd_mode else -1

    # If few resources remain, shift to blocking/denial: prefer moving closer to opponent while advancing toward resources
    block_mode = int(observation.get("remaining_resource_count", len(resources)) or len(resources)) <= 4

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            # No resources: drift toward opponent slightly (deterministic)
            v = -cheb(nx, ny, ox, oy)
        else:
            # Evaluate best (or worst) target depending on mode to change strategy materially
            # sm = our distance - opponent distance (lower is better for us if we can arrive first)
            best_sm = 10**9
            best_far = -1
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                sm = ds - do
                # Also consider how much nearer we are than opponent, and whether opponent is already very close
                if sm < best_sm:
                    best_sm = sm
                dist_from_op = cheb(ox, oy, rx, ry)
                if dist_from_op > best_far:
                    best_far = dist_from_op

            # Main objective: minimize (ds-do). Secondary: move toward a resource that opponent is not close to.
            # Mode flips secondary objective to diversify.
            sec = best_far if eps > 0 else -best_far
            # Block mode: additionally penalize moving away from the opponent path area
            v = -1000 * best_sm + 3 * sec
            if block_mode:
                v += 2 * (-cheb(nx, ny, ox, oy))
        if v > best_val:
            best_val = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]