def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    recent = set()
    path = observation.get("self_path") or []
    for p in path[-10:]:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            recent.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    adj8 = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
    def is_front(p):
        x, y = p
        if p in obstacles: return False
        for dx, dy in adj8:
            q = (x+dx, y+dy)
            if q in opp_terr:
                return True
        return False

    # Decide target: prefer flipping opponent territory adjacent cells; else unclaimed near opponent frontier
    candidates = []
    for p in opp_terr:
        if not is_front(p):  # include opponent cells themselves too
            candidates.append(p)
        else:
            candidates.append(p)
    if not candidates:
        # fallback: unclaimed that are adjacent to opponent territory
        for x, y in unclaimed:
            if is_front((x, y)):
                candidates.append((x, y))
    if not candidates:
        # final fallback: move toward nearest opponent territory cell
        candidates = list(opp_terr) if opp_terr else list(unclaimed)

    best_t = None; best_td = 10**18
    for tx, ty in candidates:
        if not inb(tx, ty): 
            continue
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_td:
            best_td = d; best_t = (tx, ty)
    if best_t is None:
        return [0, 0]

    tx, ty = best_t

    def move_score(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**12
        p = (nx, ny)
        # Immediate reward for control gain on entry
        s = 0
        if p in unclaimed: s += 70
        if p in opp_terr: s += 240
        if p in self_terr: s += 10
        # Prefer cells that are closer to target while breaking oscillations
        dist = (abs(tx - nx) + abs(ty - ny))
        s += (200 - 25 * dist)
        if p in recent:
            s -= 80
        # Push toward opponent frontier to match edge-claim archetype
        if p in unclaimed and is_front(p): s += 60
        if is_front(p): s += 40
        return s

    best_move = (0, 0); best_s = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = move_score(nx, ny)
        if sc > best_s or (sc == best_s and (dx, dy) < best_move):
            best_s = sc; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]