def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []); obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))  # Chebyshev
    if not resources:
        tx, ty = (w-1)/2, (h-1)/2
        best = None; bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = -d((nx, ny), (tx, ty)) + 0.05*d((nx, ny), (ox, oy))
            if v > bestv: bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]
    # Pick a resource where we are relatively closer than the opponent.
    best_t = resources[0]; best_adv = -10**9
    for r in resources:
        adv = d((ox, oy), r) - d((sx, sy), r)
        if adv > best_adv or (adv == best_adv and d((sx, sy), r) < d((sx, sy), best_t)):
            best_adv, best_t = adv, r
    tx, ty = best_t
    best = [0, 0]; bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        self_dist = d((nx, ny), (tx, ty))
        opp_dist = d((ox, oy), (tx, ty))
        opp_next_dist = d((ox, oy), (nx, ny))
        # Encourage reaching target faster, and keeping distance from opponent to disrupt.
        v = (opp_dist - self_dist) + 0.08*opp_next_dist - 0.02*(d((nx, ny), (tx, ty)) == 0)
        # If stepping onto a resource, strongly prefer.
        if (nx, ny) in set(tuple(p) for p in resources):
            v += 5.0
        if v > bestv:
            bestv = v; best = [dx, dy]
    return best if best is not None else [0, 0]