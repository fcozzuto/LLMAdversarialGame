def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        # Deterministic "escape" direction: move to maximize distance from opponent
        best = (-10**9, 0, 0)
        for dx, dy, nx, ny in moves:
            d = man(nx, ny, ox, oy)
            if d > best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    for dx, dy, nx, ny in moves:
        # Evaluate best target under 1-step lookahead: maximize gap reduction vs opponent
        # gap = self_dist - opp_dist; negative => we're closer.
        best_gain = -10**18
        for rx, ry in resources:
            gap_now = man(sx, sy, rx, ry) - man(ox, oy, rx, ry)
            gap_after = man(nx, ny, rx, ry) - man(ox, oy, rx, ry)
            gain = gap_now - gap_after  # positive => we improve relative position
            # Slight preference for making us actually close to the target after move
            closeness = -man(nx, ny, rx, ry) * 0.001
            v = gain + closeness
            if v > best_gain:
                best_gain = v
        # Tie-break deterministically by favoring larger immediate progress then smaller dx,dy lexicographically
        if best_gain > best[0] or (best_gain == best[0] and (dx, dy) < (best[1], best[2])):
            best = (best_gain, dx, dy)

    return [best[1], best[2]]