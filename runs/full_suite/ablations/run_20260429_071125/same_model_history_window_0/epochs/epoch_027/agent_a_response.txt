def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for king moves

    # Pick target resource where we have the most advantage (being closer)
    best_t = None
    best_adv = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        if best_t is None or adv > best_adv or (adv == best_adv and sd < dist((sx, sy), best_t)):
            best_t, best_adv = (rx, ry), adv

    if best_t is None:
        # No resources visible; just move to maximize distance from opponent toward center
        tx, ty = w // 2, h // 2
        best_t = (tx, ty)

    tx, ty = best_t
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = dist((nx, ny), (tx, ty))
        od2 = dist((nx, ny), (ox, oy))
        # Prefer decreasing distance to target, increasing distance from opponent, and avoid being stuck
        score = (od2 * 3) - sd2 * 2
        if best_score is None or score > best_score or (score == best_score and (abs(dx) + abs(dy)) < (abs(best_move[0]) + abs(best_move[1]))):
            best_score = score
            best_move = (dx, dy)

    # If we couldn't move anywhere legal (should be rare), stay still
    return [int(best_move[0]), int(best_move[1])]