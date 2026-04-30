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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cx, cy = w // 2, h // 2
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = cx, cy
        best_move = (0, 0)
        best_d = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best_move = [dx, dy]
        return best_move

    scored_resources = resources[:]
    # Deterministic tie-breaking: sort for stable behavior
    scored_resources.sort()

    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Aim to maximize the advantage over opponent on the best remaining resource
        # Advantage = (opponent distance - self distance). Higher means more likely to beat them.
        # Add small tie-break toward center to reduce dithering.
        best_for_move = -10**9
        for rx, ry in scored_resources:
            d_self = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            adv = d_op - d_self
            center_bias = -((abs(nx - cx) + abs(ny - cy)) // 2)
            val = adv * 100 + center_bias
            if val > best_for_move:
                best_for_move = val

        if best_for_move > best_score:
            best_score = best_for_move
            best_move = [dx, dy]
        elif best_for_move == best_score:
            # Stable tie-break: prefer staying if equal, else smaller dx then smaller dy
            if best_move == [0, 0] and [dx, dy] != [0, 0]:
                pass
            elif [dx, dy] == [0, 0] and best_move != [0, 0]:
                best_move = [dx, dy]
            else:
                if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                    best_move = [dx, dy]

    return best_move