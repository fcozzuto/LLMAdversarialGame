def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "").lower()
    self_is_pursuer = ("pursuer" in sr) or ("chaser" in sr) or ("hunter" in sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def best_response_for_opponent(nx, ny, their_is_pursuer):
        # If opponent is pursuer, they minimize our distance; else they maximize it.
        target_x, target_y = nx, ny
        best = None
        best_val = None
        for dx, dy in moves:
            px, py = ox + dx, oy + dy
            if not inb(px, py):
                continue
            d = dist2(px, py, target_x, target_y)
            val = -d if their_is_pursuer else d
            if best is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return best if best is not None else (0, 0)

    # Determine opponent likely role: if we are pursuer, opponent is evader; otherwise opponent is pursuer.
    opponent_is_pursuer = not self_is_pursuer

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Assume opponent makes a one-step optimal response.
        odx, ody = best_response_for_opponent(nx, ny, opponent_is_pursuer)
        npx, npy = ox + odx, oy + ody
        if not inb(npx, npy):
            npx, npy = ox, oy

        d_after = dist2(nx, ny, npx, npy)

        # If we are pursuer: minimize distance. If we are evader: maximize distance.
        score = -d_after if self_is_pursuer else d_after
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]