def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Contest resources where opponent is currently ahead.
        score = 0
        for tx, ty in resources:
            ds_now = cheb(sx, sy, tx, ty)
            do_now = cheb(ox, oy, tx, ty)
            ds_next = cheb(nx, ny, tx, ty)
            do_next = do_now  # we don't affect opponent this turn

            # We want to flip/limit opponent advantage:
            adv_now = do_now - ds_now
            adv_next = do_next - ds_next

            # Focus on resources opponent is closer to now; penalize letting them stay clearly ahead.
            if adv_now > 0:
                # If we reduce their advantage, big reward; if we worsen, penalty.
                delta = adv_now - adv_next
                if delta > 0:
                    score += 3.0 * delta
                else:
                    score += 2.5 * delta
                # Encourage not to be too far even if still behind.
                score += 0.15 * (do_next - ds_next)
            else:
                # For resources we're already closer to, just keep improving distance.
                score += 0.6 * (ds_now - ds_next)

        # Small tie-break: prefer moves that increase distance from opponent slightly
        d_op_before = cheb(sx, sy, ox, oy)
        d_op_after = cheb(nx, ny, ox, oy)
        score += 0.05 * (d_op_after - d_op_before)

        if score > best_score:
            best_score = score
            best_move = (dx if nx != sx or ny != sy else 0, dy if nx != sx or ny != sy else 0)

    return [int(best_move[0]), int(best_move[1])]