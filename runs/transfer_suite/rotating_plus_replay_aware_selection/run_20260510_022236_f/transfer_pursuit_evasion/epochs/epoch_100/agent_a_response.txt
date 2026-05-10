def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("flee" in role) or ("evasion" in role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if (sx, sy) == (ox, oy):
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dcheb(x, y):
        return max(abs(ox - x), abs(oy - y))

    def dmin_to_obstacles(x, y):
        if not obstacles:
            return 10**9
        best = 10**9
        for px, py in obstacles:
            d = abs(px - x) + abs(py - y)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    # Obstacle term: prefer staying 1-3 away; avoid 0 and very tight spots.
    def obst_score(x, y):
        d = dmin_to_obstacles(x, y)
        if d <= 0:
            return -10**6
        if d == 1:
            return 6
        if d == 2:
            return 10
        if d == 3:
            return 7
        if d == 4:
            return 3
        return 0

    best_move = [0, 0]
    best_score = -10**18 if is_evader else 10**18

    # Deterministic tie-break order: iterate fixed move list, update only on strict improvement.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        dist = dcheb(nx, ny)
        # Evader: maximize distance; also avoid being near obstacles that could be used for trapping (small d).
        # Pursuer: minimize distance; also avoid stepping onto/near obstacles too tightly.
        if is_evader:
            score = dist * 100 + obst_score(nx, ny)
            # Encourage drifting toward farthest corner when distance ties
            corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))
            corner_bonus = max(abs(cx - nx) + abs(cy - ny) for (cx, cy) in corners)
            score += corner_bonus * 0.01
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            score = -dist * 100 + obst_score(nx, ny)
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]