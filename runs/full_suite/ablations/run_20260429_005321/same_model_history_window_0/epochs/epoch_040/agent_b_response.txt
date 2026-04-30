def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b, x, y):
        dx = a - x
        dy = b - y
        return (dx*dx + dy*dy) ** 0.5

    if not resources:
        best = (-1e9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles: continue
            score = dist(nx, ny, ox, oy)
            if score > best[0]: best = (score, dx, dy)
        return [best[1], best[2]]

    # Dynamic target selection: prefer resources we can reach earlier than opponent.
    bestR = None
    bestAdv = -1e18
    for rx, ry in resources:
        adv = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
        # Add slight tie-break toward closer resources
        adv -= 0.01 * dist(sx, sy, rx, ry)
        if adv > bestAdv:
            bestAdv, bestR = adv, (rx, ry)

    rx, ry = bestR
    cand_best = (-1e18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue

        our_d = dist(nx, ny, rx, ry)
        # Resource advantage if we aim at the best attainable resource next turn
        max_adv_next = -1e18
        min_our_d_next = 1e18
        for prx, pry in resources:
            a = dist(ox, oy, prx, pry) - dist(nx, ny, prx, pry)
            # discourage stepping into opponent proximity when no advantage
            a -= 0.002 * (dist(nx, ny, ox, oy))
            if a > max_adv_next: max_adv_next = a
        # Also encourage moving toward chosen target when near-ties exist
        max_adv_next += 0.02 * (dist(sx, sy, rx, ry) - our_d)

        # Final score: maximize advantage; then minimize distance to chosen target; then avoid opponent
        score = max_adv_next - 0.05 * our_d + 0.001 * dist(nx, ny, ox, oy)
        if score > cand_best[0]:
            cand_best = (score, dx, dy)

    return [cand_best[1], cand_best[2]]