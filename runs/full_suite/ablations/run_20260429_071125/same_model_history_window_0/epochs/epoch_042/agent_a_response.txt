def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    res_set = set((x, y) for x, y in resources)
    # Choose a target resource where we have relative proximity advantage.
    best_t = None
    best_adv = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd  # positive means we're closer
        if best_t is None or adv > best_adv or (adv == best_adv and sd < dist((sx, sy), best_t)):
            best_t = (rx, ry)
            best_adv = adv

    # If no resources, drift away from opponent while avoiding obstacles.
    if best_t is None:
        tx, ty = (sx - (ox - sx), sy - (oy - sy))
        best_t = (max(0, min(w - 1, tx)), max(0, min(h - 1, ty)))

    target = best_t

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            # Engine will reject invalid moves by keeping us in place, but penalize here.
            continue

        sd = dist((nx, ny), target)
        od = dist((ox, oy), target)
        # Main objective: minimize our distance; break ties by maximizing advantage.
        score = -sd * 10 + (od - sd) * 3

        # If we step onto a resource, heavily reward.
        if (nx, ny) in res_set:
            score += 1000

        # Slightly discourage moves that give the opponent an easier path to the same target.
        score += (dist((sx, sy), target) - sd) * 1.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # Deterministic tie-break: prefer lower dx, then lower dy.
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    # If all moves invalid (unlikely), stay still.
    return [int(best_move[0]), int(best_move[1])]