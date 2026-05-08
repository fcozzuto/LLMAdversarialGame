def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_set = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            opp_set.add((int(p[0]), int(p[1])))

    def neighbors8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield nx, ny

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                unclaimed.append((x, y))

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # Pick best target deterministically.
    best_t = None
    best_val = -10**9
    for x, y in unclaimed:
        edge = (x == 0 or x == w - 1 or y == 0 or y == h - 1)
        adj_opp = 0
        for nx, ny in neighbors8(x, y):
            if (nx, ny) in opp_set:
                adj_opp = 1
                break
        # Higher is better; proximity breaks ties.
        val = (20 if adj_opp else 0) + (3 if edge else 0) - 0.01 * man(x, y, sx, sy)
        if val > best_val or (val == best_val and (best_t is None or (x, y) < best_t)):
            best_val, best_t = val, (x, y)

    if best_t is None:
        # Fallback: move toward a stable point (opposite corner from opponent).
        tx, ty = (0 if observation["opponent_position"][0] > sx else w - 1), (0 if observation["opponent_position"][1] > sy else h - 1)
    else:
        tx, ty = best_t

    # Choose move among 8 directions + stay, avoiding obstacles.
    best_move = [0, 0]
    best_score = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer decreasing distance to target, and slightly prefer stepping adjacent to opponent territory.
            dist = man(nx, ny, tx, ty)
            adj_opp = 0
            for ax, ay in neighbors8(nx, ny):
                if (ax, ay) in opp_set:
                    adj_opp = 1
                    break
            score = -dist + (0.2 if adj_opp else 0)
            if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
                best_score, best_move = score, [dx, dy]

    # If all candidate moves were blocked, stay.
    return best_move