def choose_move(observation):
    ax, ay = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles if inb(x, y))

    my_t = observation.get("self_territory") or []
    op_t = observation.get("opponent_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    my_set = set((x, y) for x, y in my_t if inb(x, y))
    op_set = set((x, y) for x, y in op_t if inb(x, y))
    un_set = set((x, y) for x, y in unclaimed if inb(x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def mindist_to_set(p, S):
        if not S:
            return 10**9
        px, py = p
        best = 10**9
        for qx, qy in S:
            dx, dy = px - qx, py - qy
            d = dx * dx + dy * dy
            if d < best:
                best = d
        return best

    targets = list(un_set) if un_set else list(op_set)
    if not targets:
        return [0, 0]
    # Deterministic choice among many: sort by (dist2, x, y) from current position
    targets.sort(key=lambda t: ((ax - t[0]) * (ax - t[0]) + (ay - t[1]) * (ay - t[1]), t[0], t[1]))
    primary_target = targets[0]

    px0, py0 = primary_target

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        p = (nx, ny)

        score = 0
        if p in un_set:
            score += 60
        if p in op_set:
            score += 45
        if p in my_set:
            score += 10

        # Bias toward the nearest unclaimed/opponent cell (primary_target)
        ddx, ddy = nx - px0, ny - py0
        score += 20 - (ddx * ddx + ddy * ddy) // 2

        # Prefer continuing toward target direction (reduce angle reversals)
        dir_now = (px0 - ax, py0 - ay)
        dir_next = (px0 - nx, py0 - ny)
        if dir_now[0] == 0 and dir_now[1] == 0:
            score += 5
        else:
            if (dir_now[0] > 0 and dir_next[0] <= 0) or (dir_now[0] < 0 and dir_next[0] >= 0):
                score -= 5
            if (dir_now[1] > 0 and dir_next[1] <= 0) or (dir_now[1] < 0 and dir_next[1] >= 0):
                score -= 5

        # If neutral, lightly prefer not to step into opponent too early unless it helps
        if (p not in un_set) and (p not in op_set) and (p not in my_set):
            score -= 5

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move