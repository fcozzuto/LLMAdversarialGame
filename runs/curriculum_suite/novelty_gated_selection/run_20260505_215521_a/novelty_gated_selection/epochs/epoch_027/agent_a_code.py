def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    rem = int(observation.get("remaining_resource_count", len(resources)))

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (man(nx, ny, cx, cy), abs(dx) + abs(dy))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        center_bias = man(nx, ny, cx, cy)  # smaller is better
        # Evaluate move by looking at the resource where it gives the best advantage
        best_adv = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # Big preference: resources where opponent is relatively far AFTER we move closer
            adv = (do - ds)
            # Mild tie-breaker: finish faster near endgame
            if rem <= 4:
                adv += (5 - ds) * 0.05
            if best_adv is None or adv > best_adv:
                best_adv = adv

        # Primary: maximize advantage, Secondary: move toward center (avoid edge traps), Tertiary: stay stable
        key = (-best_adv, center_bias, abs(dx) + abs(dy))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move