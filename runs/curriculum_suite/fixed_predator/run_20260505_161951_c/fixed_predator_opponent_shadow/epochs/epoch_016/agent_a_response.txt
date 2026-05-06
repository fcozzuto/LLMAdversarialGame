def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources, retreat to maximize distance or stay near safer corner based on opponent.
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in moves:
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestv:
                bestv = d
                best = (dx, dy)
        return [best[0], best[1]]

    # One-step lookahead with "interception pressure":
    # - Primary: maximize our post-move advantage on a target resource (opp_dist - self_dist)
    # - Secondary: prefer nearer resources (smaller self_dist) and moves that keep distance from opponent
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Choose a small candidate set of targets: closest few to us
    r_sorted = sorted(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    targets = r_sorted[:5] if len(r_sorted) > 5 else r_sorted

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        opp_next_d = man(nx, ny, ox, oy)
        worst_opp_d_for_us = 10**9
        best_r = -10**18
        for rx, ry in targets:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)  # opponent hasn't moved yet
            advantage = od - sd  # higher => we're closer than opponent after our move
            # If we can grab next (landing on it), huge bonus
            grab_bonus = 50 if (nx == rx and ny == ry) else 0
            # Penalize targets where opponent is much closer (likely to steal)
            steal_risk = 0 if od >= sd else (sd - od)  # positive when opponent behind; else 0
            val = advantage + grab_bonus - 0.15 * sd - 0.05 * opp_next_d - 0.02 * steal_risk
            if val > best_r:
                best_r = val
            if od - sd < worst_opp_d_for_us:
                worst_opp_d_for_us = od - sd

        # Encourage overall stability: not only best target, but avoid moves that make us vulnerable on the worst target.
        score = 1.0 * best_r + 0.25 * worst_opp_d_for_us
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]