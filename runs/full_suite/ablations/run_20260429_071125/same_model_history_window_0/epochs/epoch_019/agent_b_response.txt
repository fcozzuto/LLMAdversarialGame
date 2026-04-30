def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in moves if inb(x + dx, y + dy)]
    if not moves:
        return [0, 0]

    if not resources:
        # No resources: drift away from opponent deterministically
        dx = 0 if x == ox else (1 if x < ox else -1)
        dy = 0 if y == oy else (1 if y < oy else -1)
        nx, ny = x + (-dx), y + (-dy)
        for mx, my in moves:
            if (x + mx, y + my) == (nx, ny):
                return [mx, my]
        return [min(moves)[0], min(moves)[1]]

    # Choose best target resource based on who is closer (advantage = opponent_dist - self_dist)
    best_t = None
    best_adv = -10**9
    for r in resources:
        if tuple(r) in obstacles:
            continue
        r = (r[0], r[1])
        sd = dist((x, y), r)
        od = dist((ox, oy), r)
        adv = od - sd
        # Prefer targets we can reach no later than opponent; tie-break by closer to us
        if adv > best_adv or (adv == best_adv and (best_t is None or sd < dist((x, y), best_t))):
            best_adv = adv
            best_t = r

    tx, ty = best_t if best_t is not None else (x, y)

    # If opponent is strictly closer (adv < 0), prioritize blocking by moving to maximize distance from opponent while still heading toward target-ish
    aggressive = best_adv >= 0

    best_move = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        sd_next = dist((nx, ny), (tx, ty))
        od = dist((ox, oy), (tx, ty))
        adv_next = od - sd_next
        # Evaluation: primarily improve our advantage (or reduce their advantage); secondarily prefer reducing distance to target
        val = adv_next * 1000 - sd_next * 3
        if aggressive:
            # also slightly prefer increasing distance from opponent to reduce contest pressure
            val += dist((nx, ny), (ox, oy))
        else:
            # if we're behind, reduce opponent's edge by getting closer (adv_next already helps) and keep some separation
            val += dist((nx, ny), (ox, oy)) * 0.5
            # also add bias toward choosing a different nearby disputed target by looking at min distance to any resource
            # (small deterministic effect)
            minr = 10**9
            for r in resources:
                rr = (r[0], r[1])
                minr = min(minr, dist((nx, ny), rr))
            val += -minr * 1.5
        if val > best_val or (val == best_val and (best_move is None or (dx, dy) < best_move)):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]