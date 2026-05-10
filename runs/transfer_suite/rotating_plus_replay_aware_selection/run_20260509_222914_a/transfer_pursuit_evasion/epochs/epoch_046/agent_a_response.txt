def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evader" in self_role) or ("runner" in self_role) or ("evasion" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_pref = [0, 2, 6, 8, 1, 3, 5, 7, 4]  # deterministic tie-break preference

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dmin_to_obstacles(x, y):
        if not obstacles:
            return 999
        best = 999
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
                if best == 0:
                    break
        return best

    best_score = None
    best_move = (0, 0)

    for idx in dirs_pref:
        dx, dy = moves[idx]
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist = max(abs(nx - ox), abs(ny - oy))  # pursuer-friendly (diagonal)
        dob = dmin_to_obstacles(nx, ny)

        if is_evader:
            score = dist * 10.0 + dob * 1.5
            # small bias to head for farthest corner
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            score += corner_dist * 0.25
        else:
            # if can align by moving closer along x/y, slight preference
            align_bonus = 0.0
            if (nx == ox) or (ny == oy):
                align_bonus = 3.0
            score = -dist * 10.0 + dob * 0.8 + align_bonus

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]