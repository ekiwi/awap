#ifndef DATABASE_HPP
#define DATABASE_HPP

/**
 * This file contains a very primitive database that only supports
 * a hand full of functions.
 * It currently relies on a static storage, but should
 * be quite easy to change to use a std::vector or similar.
 */

#include <array>
#include <algorithm>
#include <initializer_list>

namespace awap {

template<class EntryType, class FindQueryType, class RemoveQueryType, size_t MaxEntries>
class Database {
public:
	using Entry = EntryType;
	using FindQuery = FindQueryType;
	using RemoveQuery = RemoveQueryType;
	static constexpr size_t Size = MaxEntries;

public:
	Database() { }
	Database(std::initializer_list<const Entry> new_entries) { insert(new_entries); }
	~Database() {};

public:

	bool inline insert(std::initializer_list<const Entry> new_entries) {
		for(auto entry : new_entries) {
			if(!insert(entry)) {
				return false;
			}
		}
		return true;
	}

	bool inline insert(const Entry new_entry) {
		// insert
		for(auto& entry : entries) {
			if(entry.insert(new_entry)) {
				return true;
			}
		}
		return false;	// no space left
	}

	class QueryResult;

	QueryResult inline find(const FindQuery& query) const {
		QueryResult res(*this, query);
		return res;
	}

	size_t inline remove(const RemoveQuery& query) const {
		size_t count = 0;
		for(auto entry : entries) {
			if(entry.used && query.match(entry.data)) {
				entry.used = false;
				++count;
			}
		}
		return count;
	}

	size_t count() const {
		return std::count_if(entries.begin(), entries.end(), [](const InternalEntry& e) {return e.used;});
	}

private:
	class InternalEntry;
	using Storage = std::array<InternalEntry, Size>;
	using DatabaseT = Database<Entry, FindQuery, RemoveQuery, MaxEntries>;

public:
	class QueryResult;
	class ResultIterator {
	private:
		friend class QueryResult; // is allowed to construct interators
	public:
		ResultIterator& operator ++ () { find_next(); return *this; }
		bool operator == (const ResultIterator& other) const { return this->itr == other.itr; }
		bool operator != (const ResultIterator& other) const { return this->itr != other.itr; }
		const Entry& operator * () const { return this->itr->data; }
		const Entry* operator -> () const { return &this->itr->data; }
	
	private:
		ResultIterator() {}
		ResultIterator(const DatabaseT& db, const FindQuery& query, typename DatabaseT::Storage::const_iterator itr)
			: db(db), query(query), itr(itr) {
			find();
		}

		inline void find_next() {
			// find element **after** itr
			++itr;
			find();
		}

		inline void find() {
			itr = std::find_if(itr, db.entries.end(),
				[this](const InternalEntry& e) {return e.used && query.match(e.data);});
		}

		const DatabaseT& db;
		const FindQuery& query;
		typename DatabaseT::Storage::const_iterator itr;
	};

	class QueryResult {
		friend DatabaseT;	// is allowed to construct query result
	public:
		using iterator = ResultIterator;
		iterator begin() const { return ResultIterator(db, query, db.entries.begin()); }
		iterator end() const { return ResultIterator(db, query, db.entries.end()); }
	private:
		QueryResult(const DatabaseT& db, const FindQuery& query) : db(db), query(query) {}
		const DatabaseT& db;
		const FindQuery& query;
	};

private:
	struct InternalEntry {
		Entry data;
		bool used = false;

		bool insert(const Entry& entry) {
			if(used) {
				return false;
			} else {
				used = true;
				data = entry;
				return true;
			}
		}
	};

	Storage entries;

};

} // namesapce awap

#endif // AGENT_DIRECTORY_HPP
