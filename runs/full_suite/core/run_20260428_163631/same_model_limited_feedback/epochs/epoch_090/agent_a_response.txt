def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        # No resources known: maximize distance from opponent if possible
        best = (-(10**9), [0, 0])
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                x, y = x0 + dx, y0 + dy
                if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                    d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
                    if d2 > best[0]:
                        best = (d2, [dx, dy])
        return best[1]

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Strategic change: target a resource where we have positional advantage vs opponent.
    best_res = None
    best_adv = -10**18
    for r in resources:
        if (r[0], r[1]) in obstacles:
            continue
        our = d2((x0, y0), r)
        opp = d2((ox, oy), r)
        # Favor resources we can reach sooner; tie-break by being nearer overall.
        adv = (opp - our) - 0.01 * (our)
        if adv > best_adv:
            best_adv = adv
            best_res = r
    if best_res is None:
        best_res = resources[0]

    rx, ry = best_res
    is_resource = set((x, y) for x, y in resources)

    best_score = -10**18
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = x0 + dx, y0 + dy
            if not (0 <= x < W and 0 <= y < H):
                continue
            if (x, y) in obstacles:
                continue
            move = (x, y)
            score = 0.0
            if move in is_resource:
                score += 1e6  # strong commit to immediate pickup
            # Move toward chosen resource
            score += -d2(move, (rx, ry)) * 1.0
            # Repel opponent to avoid losing contested resources
            score += d2(move, (ox, oy)) * 0.02
            # Mild penalty for moving farther from our current resource target
            score += -0.05 * (abs(dx) + abs(dy))
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move