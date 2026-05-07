def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    sx, sy = int(self_pos[0]), int(self_pos[1])
    obstacles = observation.get("obstacles", [])
    obs_set = {(int(x), int(y)) for x, y in obstacles if 0 <= int(x) < w and 0 <= int(y) < h}
    resources = observation.get("resources", [])
    if resources:
        rlist = [(int(x), int(y)) for x, y in resources if 0 <= int(x) < w and 0 <= int(y) < h]
        # nearest by Chebyshev distance; deterministic tie-break by coordinate
        best_r = None
        best_d = None
        for x, y in rlist:
            d = max(abs(x - sx), abs(y - sy))
            if best_d is None or d < best_d or (d == best_d and (x, y) < best_r):
                best_d = d
                best_r = (x, y)
        tx, ty = best_r
        moves = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                    d = max(abs(tx - nx), abs(ty - ny))
                    moves.append((d, abs(dx) + abs(dy), dx, dy))
        if moves:
            moves.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
            return [int(moves[0][2]), int(moves[0][3])]
    # No resources or all blocked: move toward center while avoiding obstacles; deterministic tie-break
    cx, cy = w // 2, h // 2
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                d = max(abs(cx - nx), abs(cy - ny))
                candidates.append((d, abs(dx) + abs(dy), dx, dy))
    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        return [int(candidates[0][2]), int(candidates[0][3])]
    return [0, 0]