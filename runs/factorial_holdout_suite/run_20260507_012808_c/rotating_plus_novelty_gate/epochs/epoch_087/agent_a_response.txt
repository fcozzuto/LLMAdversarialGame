def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose target: maximize advantage; if no advantage possible, choose closest-to-self weighted against opponent.
    best_r = None
    best_key = None
    for (rx, ry) in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        key = (adv, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    # Small "row sweep" bias: if opponent is closer on target, move to reduce their access by heading toward resources sharing our x or y.
    # Deterministic bias term based on current positions.
    bias_mode = (md(ox, oy, rx, ry) <= md(sx, sy, rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Base score: after-move advantage for the chosen target.
        sda = md(nx, ny, rx, ry)
        oda = md(ox, oy, rx, ry)
        score = (oda - sda) * 100 - sda
        # If opponent is currently at least as close to our target, add deterministic bias to "interfere".
        if bias_mode:
            # Prefer moving toward resources with same x or y as current, to slow an opponent sweep.
            bias = 0
            for (tx, ty) in resources:
                if tx == nx or ty == ny:
                    bias = max(bias, 1)
            # Also nudge toward reducing distance to best resource with shared coordinate.
            if bias:
                score += 25
            score += -(md(nx, ny, rx, ry) // 1)
        # Deterministic tie-break: prefer smaller dx, then dy, then staying.
        score -= (abs(dx) + abs(dy)) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]