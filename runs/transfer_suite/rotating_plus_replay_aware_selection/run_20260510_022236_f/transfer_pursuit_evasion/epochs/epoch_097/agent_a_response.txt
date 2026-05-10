def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cheb = lambda x, y: max(abs(ox - x), abs(oy - y))
    manh = lambda x, y: abs(ox - x) + abs(oy - y)

    def obstacle_penalty(x, y):
        if not obstacles:
            return 0
        dmin = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < dmin:
                dmin = d
        # small d => large penalty
        return 30 if dmin == 0 else (16 if dmin == 1 else (8 if dmin == 2 else (4 if dmin == 3 else 0)))

    if (sx, sy) == (ox, oy):
        return [0, 0]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Deterministic corner target for evasion/pursuit shaping
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if is_evader:
        tx, ty = max(corners, key=lambda c: manh(c[0], c[1]))
        best_score = -10**9
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = (cheb(nx, ny) * 1000) - obstacle_penalty(nx, ny) + (manh(nx, ny) * 2)
            # push toward chosen corner without breaking distance-first
            score += (-(abs(tx - nx) + abs(ty - ny)))
            # deterministic tie-break
            key = (score, -abs(dx) - abs(dy), -dx, -dy)
            if key > (best_score, -abs(best_move[0]) - abs(best_move[1]), -best_move[0], -best_move[1]):
                best_score = score
                best_move = [dx, dy]
        return best_move
    else:
        # pursuer: minimize distance, but avoid dead-end proximity to obstacles
        best_score = 10**9
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = (cheb(nx, ny) * 1000) + obstacle_penalty(nx, ny)
            # slight bias to reduce both axes (more direct capture posture)
            score += abs(ox - nx) + abs(oy - ny)
            key = (-score, -abs(dx) - abs(dy), -dx, -dy)  # higher is better
            if key > (-best_score, -abs(best_move[0]) - abs(best_move[1]), -best_move[0], -best_move[1]):
                best_score = score
                best_move = [dx, dy]
        return best_move