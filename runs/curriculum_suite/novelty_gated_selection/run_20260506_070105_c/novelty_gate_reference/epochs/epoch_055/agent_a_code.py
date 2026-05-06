def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target that we reach well while the opponent does worse.
    best_target = resources[0]
    best_tscore = -10**18
    for t in resources:
        d1 = dist((sx, sy), t)
        d2 = dist((ox, oy), t)
        # Prefer lower own distance; penalize closer opponent.
        tscore = (-d1 * 2) + (d2) + (-abs(t[0] - t[1]) * 0.01)
        if tscore > best_tscore:
            best_tscore = tscore
            best_target = t

    tx, ty = best_target

    # Evaluate next moves: maximize progress to target, avoid stepping into obstacles, and discourage giving the opponent an advantage.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd_now = dist((sx, sy), (tx, ty))
        myd_next = dist((nx, ny), (tx, ty))
        my_progress = myd_now - myd_next

        op_target_d = dist((ox, oy), (tx, ty))
        # Approximate opponent response: moving similarly reduces their distance by at most 1.
        od_reduce = 0
        if ox != tx:
            od_reduce += 1
        if oy != ty and od_reduce < 1:
            od_reduce += 1
        # Prefer moves that keep opponent farther after they likely move.
        opp_adv = op_target_d - max(op_target_d - 2, op_target_d - 1)

        # If we are closer than opponent, prioritize further progress; if not, be more defensive.
        score = my_progress * 10 + (-myd_next) * 0.5 + (opp_adv) * 0.7
        if (nx, ny) == (tx, ty):
            score += 100  # strong grab

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]