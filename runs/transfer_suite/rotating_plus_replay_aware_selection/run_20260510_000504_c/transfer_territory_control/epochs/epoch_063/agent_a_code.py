def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    def best_target(candidates):
        if not candidates:
            return None
        best = None
        best_key = None
        for (tx, ty) in candidates:
            if (tx, ty) in obstacles:
                continue
            d = abs(tx - sx) + abs(ty - sy)
            # deterministic tie-break: closer first, then lowest x, then lowest y
            key = (d, tx, ty)
            if best_key is None or key < best_key:
                best_key = key
                best = (tx, ty)
        return best

    target = best_target(resources)
    if target is None:
        near = []
        for (x, y) in self_terr:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed and (nx, ny) not in obstacles:
                        near.append((nx, ny))
        target = best_target(near)
    if target is None:
        target = best_target(unclaimed) or best_target(self_terr) or best_target(opp_terr) or (sx, sy)

    tx, ty = target
    dx = 0
    dy = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        # fallback: deterministic scan for any safe move that reduces manhattan distance
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (10**9, 0, 0)
        for mdx, mdy in moves:
            px, py = sx + mdx, sy + mdy
            if not (0 <= px < w and 0 <= py < h) or (px, py) in obstacles:
                continue
            score = abs(tx - px) + abs(ty - py)
            key = (score, mdx, mdy)
            if key < best:
                best = key
        return [best[1], best[2]]

    return [dx, dy]