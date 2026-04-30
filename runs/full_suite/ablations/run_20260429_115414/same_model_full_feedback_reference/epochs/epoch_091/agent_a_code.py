def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    has_res = bool(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        opp_dist = cheb(nx, ny, ox, oy)

        if has_res:
            # Pick moves that secure resources where we arrive no later than opponent, and keep distance from opponent.
            score = -0.25 * opp_dist
            # Deterministic tie-break: iterate resources in given order.
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # If we can reach at least as fast this turn onward, prioritize.
                # do-ds positive => our advantage; also prefer closer overall ds.
                adv = do - ds
                if adv >= 0:
                    score += 50 * adv - 2 * ds
                else:
                    # Still allow contesting but much less.
                    score += 0.2 * adv - 1.2 * ds
            # Also slightly prefer moving toward the "front" (diagonal to opponent corner) to keep momentum.
            front = cheb(nx, ny, W - 1 - ox, H - 1 - oy)
            score -= 0.02 * front
        else:
            # No resources: move toward center of opponent line while keeping distance.
            score = -0.25 * opp_dist + 0.03 * cheb(nx, ny, (W - 1) // 2, (H - 1) // 2)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]