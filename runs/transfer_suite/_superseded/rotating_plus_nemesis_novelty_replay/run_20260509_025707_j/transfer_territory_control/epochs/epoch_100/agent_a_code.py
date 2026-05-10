def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obs = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs)
    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((p[0], p[1]) for p in unclaimed)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in un_set:
            score += 100000
        score += - (abs(ox - nx) + abs(oy - ny))  # approach opponent/front
        score += -0.5 * (abs(nx - sx) + abs(ny - sy))  # avoid moving unnecessarily
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best_score == -10**18:
        return [0, 0]
    return best