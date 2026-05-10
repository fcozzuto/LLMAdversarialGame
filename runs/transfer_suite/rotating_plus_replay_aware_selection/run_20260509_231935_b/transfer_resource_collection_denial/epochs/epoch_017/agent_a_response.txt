def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
    turns = observation.get("turns_remaining", 0)
    rem = observation.get("remaining_resource_count", len(resources))

    best_move = (0, 0)
    best_val = -10**18

    # If no visible resources, drift toward center while minimizing opponent approach
    if not resources:
        cx, cy = w // 2, h // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            v = -dist8(nx, ny, cx, cy) + 0.5 * dist8(nx, ny, ox, oy)
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Evaluate moves by best attainable "collection opportunity"
    # Favor resources where we beat the opponent in travel time.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        move_val = 0.0
        # Focus on top few resources deterministically for speed/consistency
        scored = []
        for rx, ry in resources:
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            adv = od - sd  # positive => we arrive earlier
            # Larger remaining resources => slightly more opportunistic; low turns => commit harder
            k = 1.0 + (0.6 if rem <= 6 else 0.2)
            if turns <= 6:
                k *= 1.6
            # Tie/close competition: still prefer nearer and safer advantage
            val = k * (adv * 10.0 + (1.5 if adv > 0 else 0.0)) - 0.12 * sd
            # Small penalty if opponent is already extremely close and adv is not positive
            if adv <= 0 and od <= 1:
                val -= 3.0
            scored.append((val, sd, adv, rx, ry))
        scored.sort(key=lambda t: (-(t[0]), t[1], -t[2], t[3], t[4]))
        topk = 3 if turns > 10 else 2
        for i in range(min(topk, len(scored))):
            move_val += scored[i][0] * (1.0 if i == 0 else 0.55)

        # Extra bias: if we can step onto a resource, strongly commit
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            move_val += 50.0 + 0.01 * turns

        if move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]