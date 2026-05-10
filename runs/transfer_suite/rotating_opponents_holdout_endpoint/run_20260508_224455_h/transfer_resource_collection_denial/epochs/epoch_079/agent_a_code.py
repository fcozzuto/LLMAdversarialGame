def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Target: close to self, but not one the opponent is much closer to.
    best_t = None
    best_sc = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        sc = (-ds) + 0.8 * (do - ds)  # prioritize reducing ds; penalize being less competitive
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    best_m = (0, 0)
    best_ms = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            ms = -10**12
        else:
            new_ds = manh(nx, ny, tx, ty)
            new_do = manh(nx, ny, ox, oy)
            cur_ds = manh(sx, sy, tx, ty)
            cur_do = manh(sx, sy, ox, oy)

            # Aim to reduce distance to target, while not allowing opponent to gain ground too much.
            # Also lightly prefer improving when already tied.
            ms = (-new_ds) + 0.35 * (new_do - cur_do) + 0.15 * (cur_ds - new_ds)

            # If we step onto the exact target cell, strong boost.
            if nx == tx and ny == ty:
                ms += 1000

            # Discourage moving adjacent to opponent when target isn't immediately reached.
            if (new_do <= 2) and not (nx == tx and ny == ty):
                ms -= 5

        if ms > best_ms:
            best_ms = ms
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]